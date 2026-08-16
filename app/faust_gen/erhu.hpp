/* ------------------------------------------------------------
name: "erhu"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Erhu -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Erhu_H__
#define  __Erhu_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Erhu
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

class ErhuSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec7[2];
	
  public:
	
	int getNumInputsErhuSIG0() {
		return 0;
	}
	int getNumOutputsErhuSIG0() {
		return 1;
	}
	
	void instanceInitErhuSIG0(int sample_rate) {
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iVec2[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec7[l7] = 0;
		}
	}
	
	void fillErhuSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec7[0] = (iVec2[1] + iRec7[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec7[0]));
			iVec2[1] = iVec2[0];
			iRec7[1] = iRec7[0];
		}
	}

};

static ErhuSIG0* newErhuSIG0() { return (ErhuSIG0*)new ErhuSIG0(); }
static void deleteErhuSIG0(ErhuSIG0* dsp) { delete dsp; }

static float Erhu_faustpower2_f(float value) {
	return value * value;
}
static float Erhu_faustpower3_f(float value) {
	return value * value * value;
}
static float Erhu_faustpower4_f(float value) {
	return value * value * value * value;
}
static float ftbl0ErhuSIG0[65536];

class Erhu : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	float fConst1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fConst4;
	float fConst6;
	float fConst7;
	float fConst8;
	float fConst9;
	float fConst10;
	float fConst11;
	float fConst12;
	float fConst13;
	float fConst14;
	float fConst15;
	int iRec4[2];
	FAUSTFLOAT fHslider4;
	float fRec3[5];
	FAUSTFLOAT fHslider5;
	float fRec8[2];
	float fConst16;
	float fConst17;
	FAUSTFLOAT fHslider6;
	float fRec5[2];
	float fRec2[3];
	FAUSTFLOAT fHslider7;
	float fRec9[3];
	FAUSTFLOAT fHslider8;
	
 public:
	Erhu() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Erhu -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "erhu.dsp");
		m->declare("filters.lib/bandpass0_bandstop1:author", "Julius O. Smith III");
		m->declare("filters.lib/bandpass0_bandstop1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/bandpass0_bandstop1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/bandpass:author", "Julius O. Smith III");
		m->declare("filters.lib/bandpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/bandpass:license", "MIT-style STK-4.3 license");
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
		m->declare("filters.lib/tf2sb:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2sb:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2sb:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "erhu");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		ErhuSIG0* sig0 = newErhuSIG0();
		sig0->instanceInitErhuSIG0(sample_rate);
		sig0->fillErhuSIG0(65536, ftbl0ErhuSIG0);
		deleteErhuSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.1f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst2 = 3.1415927f / fConst0;
		fConst3 = 4.0f * Erhu_faustpower2_f(fConst0);
		fConst4 = 1.0f / fConst0;
		float fConst5 = Erhu_faustpower3_f(fConst4);
		fConst6 = 2.828427f * fConst5;
		fConst7 = 11.313708f / fConst0;
		fConst8 = 0.5f / fConst0;
		fConst9 = 2.0f * fConst0;
		fConst10 = Erhu_faustpower2_f(fConst4);
		fConst11 = Erhu_faustpower4_f(fConst4);
		fConst12 = 5.656854f * fConst5;
		fConst13 = 22.627417f / fConst0;
		fConst14 = 4.0f * fConst11;
		fConst15 = 6.0f * fConst11;
		fConst16 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst17 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.2f);
		fHslider1 = FAUSTFLOAT(0.06f);
		fHslider2 = FAUSTFLOAT(3.5e+03f);
		fHslider3 = FAUSTFLOAT(293.0f);
		fHslider4 = FAUSTFLOAT(0.35f);
		fHslider5 = FAUSTFLOAT(5.5f);
		fHslider6 = FAUSTFLOAT(0.012f);
		fHslider7 = FAUSTFLOAT(1.4e+03f);
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
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec4[l4] = 0;
		}
		for (int l5 = 0; l5 < 5; l5 = l5 + 1) {
			fRec3[l5] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec8[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec5[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec2[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
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
	
	virtual Erhu* clone() {
		return new Erhu();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("erhu");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.06f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bow", &fHslider4, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("bright", &fHslider2, FAUSTFLOAT(3.5e+03f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(7e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("formant", &fHslider7, FAUSTFLOAT(1.4e+03f), FAUSTFLOAT(6e+02f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(293.0f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.2f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider5, FAUSTFLOAT(5.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider6, FAUSTFLOAT(0.012f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.04f), FAUSTFLOAT(0.0001f));
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
		float fSlow5 = std::tan(fConst2 * float(fHslider2));
		float fSlow6 = 2.0f * (1.0f - 1.0f / Erhu_faustpower2_f(fSlow5));
		float fSlow7 = 1.0f / fSlow5;
		float fSlow8 = (fSlow7 + -1.4142135f) / fSlow5 + 1.0f;
		float fSlow9 = (fSlow7 + 1.4142135f) / fSlow5 + 1.0f;
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = float(fHslider3);
		float fSlow12 = std::tan(fConst2 * std::min<float>(8e+03f, 4.0f * fSlow11));
		float fSlow13 = std::sqrt(fConst3 * std::tan(fConst2 * std::max<float>(6e+01f, 0.5f * fSlow11)) * fSlow12);
		float fSlow14 = Erhu_faustpower2_f(fSlow13);
		float fSlow15 = fConst9 * fSlow12 - fConst8 * (fSlow14 / fSlow12);
		float fSlow16 = fSlow15 * (fConst7 + fConst6 * fSlow14);
		float fSlow17 = Erhu_faustpower2_f(fSlow15);
		float fSlow18 = Erhu_faustpower4_f(fSlow13);
		float fSlow19 = fConst11 * fSlow18 + fConst10 * (4.0f * fSlow17 + 8.0f * fSlow14);
		float fSlow20 = fSlow19 + (16.0f - fSlow16);
		float fSlow21 = fConst12 * fSlow14;
		float fSlow22 = fConst14 * fSlow18;
		float fSlow23 = fSlow22 + fSlow15 * (fConst13 - fSlow21) + -64.0f;
		float fSlow24 = fConst15 * fSlow18 + (96.0f - fConst10 * (8.0f * fSlow17 + 16.0f * fSlow14));
		float fSlow25 = fSlow22 + fSlow15 * (fSlow21 - fConst13) + -64.0f;
		float fSlow26 = fSlow16 + fSlow19 + 16.0f;
		float fSlow27 = 1.0f / fSlow26;
		float fSlow28 = 1.3969839e-10f * float(fHslider4);
		float fSlow29 = fConst10 * (fSlow17 / fSlow26);
		float fSlow30 = fConst4 * float(fHslider5);
		float fSlow31 = float(fHslider6);
		float fSlow32 = 0.6f / fSlow9;
		float fSlow33 = std::tan(fConst2 * float(fHslider7));
		float fSlow34 = 2.0f * (1.0f - 1.0f / Erhu_faustpower2_f(fSlow33));
		float fSlow35 = 1.0f / fSlow33;
		float fSlow36 = (fSlow35 + -0.5555556f) / fSlow33 + 1.0f;
		float fSlow37 = (fSlow35 + 0.5555556f) / fSlow33 + 1.0f;
		float fSlow38 = 1.0f / fSlow37;
		float fSlow39 = 0.5f / (fSlow33 * fSlow37);
		float fSlow40 = 0.45f * float(fHslider8);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			fRec3[0] = fSlow28 * float(iRec4[0]) - fSlow27 * (fSlow25 * fRec3[1] + fSlow24 * fRec3[2] + fSlow23 * fRec3[3] + fSlow20 * fRec3[4]);
			float fTemp1 = ((1 - iVec0[1]) ? 0.0f : fSlow30 + fRec8[1]);
			fRec8[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = std::max<float>(1.1920929e-07f, std::fabs(fSlow11 * (fSlow31 * std::max<float>(0.0f, std::min<float>(fConst17 * fRec1[0], 1.0f) - fConst16 * fTemp0) * ftbl0ErhuSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 1.0f)));
			float fTemp3 = fRec5[1] + fConst4 * fTemp2;
			float fTemp4 = fTemp3 + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			fRec5[0] = ((iTemp5) ? fTemp3 : fTemp4);
			float fRec6 = ((iTemp5) ? fTemp3 : fTemp3 + fTemp4 * (1.0f - fConst0 / fTemp2));
			fRec2[0] = 2.0f * fRec6 + fSlow29 * (4.0f * fRec3[0] - 8.0f * fRec3[2] + 4.0f * fRec3[4]) + (-1.0f - fSlow10 * (fSlow8 * fRec2[2] + fSlow6 * fRec2[1]));
			float fTemp6 = fRec2[2] + fRec2[0] + 2.0f * fRec2[1];
			fRec9[0] = fSlow10 * fTemp6 - fSlow38 * (fSlow36 * fRec9[2] + fSlow34 * fRec9[1]);
			float fTemp7 = fSlow40 * (fSlow39 * (fRec9[0] - fRec9[2]) + fSlow32 * fTemp6) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fConst1 * (fSlow3 - fRec1[0]) + 1.0f, 0.9f)) * (1.0f - fSlow2 * fTemp0));
			output0[i0] = FAUSTFLOAT(fTemp7);
			output1[i0] = FAUSTFLOAT(fTemp7);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			for (int j0 = 4; j0 > 0; j0 = j0 - 1) {
				fRec3[j0] = fRec3[j0 - 1];
			}
			fRec8[1] = fRec8[0];
			fRec5[1] = fRec5[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
		}
	}

};

#endif
