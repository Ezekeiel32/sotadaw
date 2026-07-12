/* ------------------------------------------------------------
name: "wt_morph"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn WtMorph -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __WtMorph_H__
#define  __WtMorph_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS WtMorph
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class WtMorphSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec5[2];
	
  public:
	
	int getNumInputsWtMorphSIG0() {
		return 0;
	}
	int getNumOutputsWtMorphSIG0() {
		return 1;
	}
	
	void instanceInitWtMorphSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec5[l6] = 0;
		}
	}
	
	void fillWtMorphSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec5[0] = (iVec2[1] + iRec5[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec5[0]));
			iVec2[1] = iVec2[0];
			iRec5[1] = iRec5[0];
		}
	}

};

static WtMorphSIG0* newWtMorphSIG0() { return (WtMorphSIG0*)new WtMorphSIG0(); }
static void deleteWtMorphSIG0(WtMorphSIG0* dsp) { delete dsp; }

static float WtMorph_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0WtMorphSIG0[65536];

class WtMorph : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	FAUSTFLOAT fHslider1;
	float fRec3[2];
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fRec4[2];
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fConst4;
	float fRec6[2];
	float fConst5;
	float fConst6;
	float fRec7[2];
	float fConst7;
	float fRec8[2];
	float fConst8;
	float fRec9[2];
	float fConst9;
	float fRec10[2];
	float fRec11[2];
	float fConst10;
	float fRec12[2];
	float fConst11;
	float fRec13[2];
	float fConst12;
	float fRec14[2];
	FAUSTFLOAT fHslider6;
	float fVec3[2];
	float fRec1[2];
	float fRec0[3];
	
 public:
	WtMorph() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn WtMorph -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "wt_morph.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "wt_morph");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/lf_triangle:author", "Bart Brouns");
		m->declare("oscillators.lib/lf_triangle:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw1:author", "Bart Brouns");
		m->declare("oscillators.lib/saw1:licence", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		WtMorphSIG0* sig0 = newWtMorphSIG0();
		sig0->instanceInitWtMorphSIG0(sample_rate);
		sig0->fillWtMorphSIG0(65536, ftbl0WtMorphSIG0);
		deleteWtMorphSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 0.15f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst3 = 1.0f / fConst0;
		fConst4 = 8.0f / fConst0;
		fConst5 = 0.45f * fConst0;
		fConst6 = 7.0f / fConst0;
		fConst7 = 4.0f / fConst0;
		fConst8 = 3.0f / fConst0;
		fConst9 = 2.0f / fConst0;
		fConst10 = 5.0f / fConst0;
		fConst11 = 6.0f / fConst0;
		fConst12 = 9.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(9e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.35f);
		fHslider2 = FAUSTFLOAT(0.005f);
		fHslider3 = FAUSTFLOAT(0.0f);
		fHslider4 = FAUSTFLOAT(0.5f);
		fHslider5 = FAUSTFLOAT(2.2e+02f);
		fHslider6 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec4[l4] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec11[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec12[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec13[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec14[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fVec3[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fRec1[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 3; l18 = l18 + 1) {
			fRec0[l18] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual WtMorph* clone() {
		return new WtMorph();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("wt_morph");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.005f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(9e+03f), FAUSTFLOAT(5e+02f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider5, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("motion", &fHslider3, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("wave", &fHslider4, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / WtMorph_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.0f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.0f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		int iSlow7 = fSlow6 == 0.0f;
		float fSlow8 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow9 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = float(fHslider3);
		float fSlow12 = fConst3 * std::max<float>(fSlow11, 0.001f);
		float fSlow13 = float(fSlow11 > 0.0f);
		float fSlow14 = float(fHslider4);
		float fSlow15 = float(fHslider5);
		float fSlow16 = fConst4 * fSlow15;
		float fSlow17 = 0.11f * float((8.0f * fSlow15) < fConst5);
		float fSlow18 = fConst6 * fSlow15;
		float fSlow19 = float((7.0f * fSlow15) < fConst5);
		float fSlow20 = 0.14f * fSlow19;
		float fSlow21 = fConst7 * fSlow15;
		float fSlow22 = float((4.0f * fSlow15) < fConst5);
		float fSlow23 = 0.27f * fSlow22;
		float fSlow24 = fConst8 * fSlow15;
		float fSlow25 = float((3.0f * fSlow15) < fConst5);
		float fSlow26 = 0.36f * fSlow25;
		float fSlow27 = fConst9 * fSlow15;
		float fSlow28 = float((2.0f * fSlow15) < fConst5);
		float fSlow29 = 0.52f * fSlow28;
		float fSlow30 = fConst3 * fSlow15;
		float fSlow31 = float(fSlow15 < fConst5);
		float fSlow32 = fConst10 * fSlow15;
		float fSlow33 = 0.22f * float((5.0f * fSlow15) < fConst5);
		float fSlow34 = fConst11 * fSlow15;
		float fSlow35 = 0.17f * float((6.0f * fSlow15) < fConst5);
		float fSlow36 = fConst12 * fSlow15;
		float fSlow37 = 0.07f * float((9.0f * fSlow15) < fConst5);
		float fSlow38 = 0.12f * fSlow19;
		float fSlow39 = 0.42f * fSlow25;
		float fSlow40 = 0.04f * fSlow22;
		float fSlow41 = 0.09f * fSlow25;
		float fSlow42 = 0.28f * fSlow28;
		float fSlow43 = 0.45454547f * float(fHslider6);
		float fSlow44 = 1.0f - fSlow2;
		float fSlow45 = 1.0f / (fSlow2 + 1.0f);
		float fSlow46 = 0.82f / fSlow4;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow6;
			iRec2[0] = iSlow7 * (iRec2[1] + 1);
			fRec3[0] = fSlow6 + fRec3[1] * float(fVec1[1] >= fSlow6);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow12 + fRec4[1]);
			fRec4[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = std::min<float>(2.0f, std::max<float>(0.0f, fSlow14 + fSlow13 * (2.0f * (1.0f - std::fabs(2.0f * fRec4[0] + -1.0f)) + -1.0f)));
			float fTemp3 = ((iTemp0) ? 0.0f : fSlow16 + fRec6[1]);
			fRec6[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = ((iTemp0) ? 0.0f : fSlow18 + fRec7[1]);
			fRec7[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))];
			float fTemp6 = ((iTemp0) ? 0.0f : fSlow21 + fRec8[1]);
			fRec8[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))];
			float fTemp8 = ((iTemp0) ? 0.0f : fSlow24 + fRec9[1]);
			fRec9[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))];
			float fTemp10 = ((iTemp0) ? 0.0f : fSlow27 + fRec10[1]);
			fRec10[0] = fTemp10 - std::floor(fTemp10);
			float fTemp11 = ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))];
			float fTemp12 = ((iTemp0) ? 0.0f : fSlow30 + fRec11[1]);
			fRec11[0] = fTemp12 - std::floor(fTemp12);
			float fTemp13 = fSlow31 * ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec11[0]), 65535))];
			float fTemp14 = ((iTemp0) ? 0.0f : fSlow32 + fRec12[1]);
			fRec12[0] = fTemp14 - std::floor(fTemp14);
			float fTemp15 = fSlow33 * ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))];
			float fTemp16 = ((iTemp0) ? 0.0f : fSlow34 + fRec13[1]);
			fRec13[0] = fTemp16 - std::floor(fTemp16);
			float fTemp17 = std::max<float>(fTemp2 + -1.0f, 0.0f);
			float fTemp18 = ((iTemp0) ? 0.0f : fSlow36 + fRec14[1]);
			fRec14[0] = fTemp18 - std::floor(fTemp18);
			float fTemp19 = fTemp13 + fSlow39 * fTemp9 + fTemp15 + fSlow38 * fTemp5 + fSlow37 * ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec14[0]), 65535))];
			float fTemp20 = std::min<float>(fTemp2, 1.0f);
			float fTemp21 = fSlow43 * (((fTemp13 + fSlow42 * fTemp11 + fSlow41 * fTemp9 + fSlow40 * fTemp7) * (1.0f - fTemp20) + fTemp20 * fTemp19) * float(fTemp2 <= 1.0f) + (fTemp19 * (1.0f - fTemp17) + fTemp17 * (fSlow35 * ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec13[0]), 65535))] + fTemp15 + fTemp13 + fSlow29 * fTemp11 + fSlow26 * fTemp9 + fSlow23 * fTemp7 + fSlow20 * fTemp5 + fSlow17 * ftbl0WtMorphSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))])) * float(fTemp2 > 1.0f)) * std::max<float>(0.0f, std::min<float>(fSlow10 * fRec3[0], std::max<float>(fConst2 * (fSlow9 - fRec3[0]) + 1.0f, 0.85f)) * (1.0f - fSlow8 * float(iRec2[0])));
			fVec3[0] = fTemp21;
			fRec1[0] = -(fSlow45 * (fSlow44 * fRec1[1] - (fTemp21 + fVec3[1])));
			fRec0[0] = fRec1[0] - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp22 = fSlow46 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp22);
			output1[i0] = FAUSTFLOAT(fTemp22);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec11[1] = fRec11[0];
			fRec12[1] = fRec12[0];
			fRec13[1] = fRec13[0];
			fRec14[1] = fRec14[0];
			fVec3[1] = fVec3[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
