/* ------------------------------------------------------------
name: "ney"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Ney -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Ney_H__
#define  __Ney_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Ney
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

class NeySIG0 {
	
  private:
	
	int iVec2[2];
	int iRec6[2];
	
  public:
	
	int getNumInputsNeySIG0() {
		return 0;
	}
	int getNumOutputsNeySIG0() {
		return 1;
	}
	
	void instanceInitNeySIG0(int sample_rate) {
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iVec2[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec6[l9] = 0;
		}
	}
	
	void fillNeySIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec6[0] = (iVec2[1] + iRec6[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec6[0]));
			iVec2[1] = iVec2[0];
			iRec6[1] = iRec6[0];
		}
	}

};

static NeySIG0* newNeySIG0() { return (NeySIG0*)new NeySIG0(); }
static void deleteNeySIG0(NeySIG0* dsp) { delete dsp; }

static float Ney_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0NeySIG0[65536];

class Ney : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	float fConst3;
	int iRec1[2];
	FAUSTFLOAT fHslider0;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	float fConst4;
	FAUSTFLOAT fHslider2;
	float fConst5;
	FAUSTFLOAT fHslider3;
	float fConst6;
	int iRec5[2];
	float fRec4[3];
	float fRec3[3];
	FAUSTFLOAT fHslider4;
	float fConst7;
	float fConst8;
	float fConst9;
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	float fConst10;
	float fRec8[2];
	FAUSTFLOAT fHslider7;
	float fConst11;
	float fRec7[2];
	float fConst12;
	float fRec9[2];
	float fRec10[2];
	FAUSTFLOAT fHslider8;
	
 public:
	Ney() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Ney -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "ney.dsp");
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
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "ney");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
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
		NeySIG0* sig0 = newNeySIG0();
		sig0->instanceInitNeySIG0(sample_rate);
		sig0->fillNeySIG0(65536, ftbl0NeySIG0);
		deleteNeySIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst4 = 0.18f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst5 = 3.1415927f / fConst0;
		fConst6 = 3.7699113f / fConst0;
		fConst7 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst10 = 1.0f / fConst0;
		fConst11 = 3.0f / fConst0;
		fConst12 = 2.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.2f);
		fHslider1 = FAUSTFLOAT(0.06f);
		fHslider2 = FAUSTFLOAT(5e+03f);
		fHslider3 = FAUSTFLOAT(392.0f);
		fHslider4 = FAUSTFLOAT(0.55f);
		fHslider5 = FAUSTFLOAT(0.02f);
		fHslider6 = FAUSTFLOAT(5.0f);
		fHslider7 = FAUSTFLOAT(0.009f);
		fHslider8 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec5[l5] = 0;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec7[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec10[l13] = 0.0f;
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
	
	virtual Ney* clone() {
		return new Ney();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("ney");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.06f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("breath", &fHslider4, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.1f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(392.0f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("grace", &fHslider5, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.1f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.2f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider6, FAUSTFLOAT(5.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider7, FAUSTFLOAT(0.009f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("warmth", &fHslider2, FAUSTFLOAT(5e+03f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(9e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = std::tan(fConst5 * float(fHslider2));
		float fSlow6 = 2.0f * (1.0f - 1.0f / Ney_faustpower2_f(fSlow5));
		float fSlow7 = 1.0f / fSlow5;
		float fSlow8 = (fSlow7 + -1.4142135f) / fSlow5 + 1.0f;
		float fSlow9 = (fSlow7 + 1.4142135f) / fSlow5 + 1.0f;
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = float(fHslider3);
		float fSlow12 = std::tan(fConst6 * fSlow11);
		float fSlow13 = 2.0f * (1.0f - 1.0f / Ney_faustpower2_f(fSlow12));
		float fSlow14 = 1.0f / fSlow12;
		float fSlow15 = (fSlow14 + -0.625f) / fSlow12 + 1.0f;
		float fSlow16 = (fSlow14 + 0.625f) / fSlow12 + 1.0f;
		float fSlow17 = 1.0f / fSlow16;
		float fSlow18 = 1.0f / (fSlow12 * fSlow16);
		float fSlow19 = 0.7f * (float(fHslider4) / fSlow9);
		float fSlow20 = float(fHslider5);
		float fSlow21 = fConst10 * float(fHslider6);
		float fSlow22 = float(fHslider7);
		float fSlow23 = fConst11 * fSlow11;
		float fSlow24 = fConst12 * fSlow11;
		float fSlow25 = fConst10 * fSlow11;
		float fSlow26 = 0.6f * float(fHslider8);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec0[1] + (iRec0[1] > 0));
			float fTemp0 = float(iRec0[0]);
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec1[1] >= fSlow0);
			float fTemp1 = std::max<float>(0.0f, std::min<float>(fSlow4 * fRec2[0], std::max<float>(fConst4 * (fSlow3 - fRec2[0]) + 1.0f, 0.82f)) * (1.0f - fSlow2 * float(iRec1[0])));
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			fRec4[0] = 4.656613e-10f * float(iRec5[0]) - fSlow17 * (fSlow15 * fRec4[2] + fSlow13 * fRec4[1]);
			fRec3[0] = fSlow18 * (fRec4[0] - fRec4[2]) - fSlow10 * (fSlow8 * fRec3[2] + fSlow6 * fRec3[1]);
			int iTemp2 = 1 - iVec0[1];
			float fTemp3 = ((iTemp2) ? 0.0f : fSlow21 + fRec8[1]);
			fRec8[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = (fSlow22 * ftbl0NeySIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 1.0f) * (1.0f - fSlow20 * std::max<float>(0.0f, std::min<float>(fConst8 * fTemp0, fConst9 * (fConst7 - fTemp0) + 1.0f)));
			float fTemp5 = ((iTemp2) ? 0.0f : fRec7[1] + fSlow23 * fTemp4);
			fRec7[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp2) ? 0.0f : fRec9[1] + fSlow24 * fTemp4);
			fRec9[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp2) ? 0.0f : fRec10[1] + fSlow25 * fTemp4);
			fRec10[0] = fTemp7 - std::floor(fTemp7);
			float fTemp8 = fSlow26 * (0.6f * (ftbl0NeySIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] + 0.12f * ftbl0NeySIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + 0.06f * ftbl0NeySIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))]) * fTemp1 + fSlow19 * (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) * (fTemp1 + 0.5f * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fConst3 * (fConst1 - fTemp0) + 1.0f))));
			output0[i0] = FAUSTFLOAT(fTemp8);
			output1[i0] = FAUSTFLOAT(fTemp8);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			iRec5[1] = iRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec8[1] = fRec8[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
		}
	}

};

#endif
