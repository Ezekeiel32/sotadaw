/* ------------------------------------------------------------
name: "gamelan_gong"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn GamelanGong -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __GamelanGong_H__
#define  __GamelanGong_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS GamelanGong
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

class GamelanGongSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec6[2];
	
  public:
	
	int getNumInputsGamelanGongSIG0() {
		return 0;
	}
	int getNumOutputsGamelanGongSIG0() {
		return 1;
	}
	
	void instanceInitGamelanGongSIG0(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec2[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
	}
	
	void fillGamelanGongSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec6[0] = (iVec2[1] + iRec6[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec6[0]));
			iVec2[1] = iVec2[0];
			iRec6[1] = iRec6[0];
		}
	}

};

static GamelanGongSIG0* newGamelanGongSIG0() { return (GamelanGongSIG0*)new GamelanGongSIG0(); }
static void deleteGamelanGongSIG0(GamelanGongSIG0* dsp) { delete dsp; }

static float GamelanGong_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0GamelanGongSIG0[65536];

class GamelanGong : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fHslider0;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec3[2];
	FAUSTFLOAT fHslider1;
	float fRec1[3];
	int iRec4[2];
	float fConst11;
	float fConst12;
	float fRec5[2];
	float fConst13;
	float fConst14;
	FAUSTFLOAT fHslider2;
	float fConst15;
	FAUSTFLOAT fHslider3;
	float fConst16;
	float fRec7[2];
	float fConst17;
	float fConst18;
	float fConst19;
	float fConst20;
	float fConst21;
	float fRec8[2];
	float fConst22;
	float fConst23;
	float fConst24;
	FAUSTFLOAT fHslider4;
	float fConst25;
	float fRec9[2];
	float fRec10[2];
	FAUSTFLOAT fHslider5;
	float fRec0[3];
	float fConst26;
	
 public:
	GamelanGong() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn GamelanGong -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "gamelan_gong.dsp");
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
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "gamelan_gong");
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
		GamelanGongSIG0* sig0 = newGamelanGongSIG0();
		sig0->instanceInitGamelanGongSIG0(sample_rate);
		sig0->fillGamelanGongSIG0(65536, ftbl0GamelanGongSIG0);
		deleteGamelanGongSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(7853.9814f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / GamelanGong_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.4142135f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 18.849556f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.02f * fConst0);
		fConst11 = 0.2f * fConst0;
		fConst12 = 1.0f / std::max<float>(1.0f, fConst11);
		fConst13 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst14 = 1.0f / fConst13;
		fConst15 = 1.0f / std::max<float>(1.0f, 0.5f * fConst0);
		fConst16 = 4.13f / fConst0;
		fConst17 = 0.4f * fConst0;
		fConst18 = 1.0f / std::max<float>(1.0f, fConst17);
		fConst19 = std::max<float>(1.0f, 0.003f * fConst0);
		fConst20 = 1.0f / fConst19;
		fConst21 = 2.38f / fConst0;
		fConst22 = 1.0f / std::max<float>(1.0f, fConst0);
		fConst23 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst24 = 1.0f / fConst23;
		fConst25 = 1.0f / fConst0;
		fConst26 = 0.887f / fConst5;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(65.4f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.4f);
		fHslider2 = FAUSTFLOAT(6.0f);
		fHslider3 = FAUSTFLOAT(0.045f);
		fHslider4 = FAUSTFLOAT(0.9f);
		fHslider5 = FAUSTFLOAT(0.55f);
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
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec10[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec0[l13] = 0.0f;
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
	
	virtual GamelanGong* clone() {
		return new GamelanGong();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("gamelan_gong");
		ui_interface->addHorizontalSlider("boom", &fHslider1, FAUSTFLOAT(0.4f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(65.4f), FAUSTFLOAT(25.0f), FAUSTFLOAT(4e+02f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("glide", &fHslider3, FAUSTFLOAT(0.045f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.15f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("ombak", &fHslider4, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.0f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.05f));
		ui_interface->addHorizontalSlider("tail", &fHslider2, FAUSTFLOAT(6.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst7 * fSlow0);
		float fSlow2 = 2.0f * (1.0f - 1.0f / GamelanGong_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -0.5f) / fSlow1 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 0.5f) / fSlow1 + 1.0f);
		float fSlow6 = float(fButton0);
		float fSlow7 = 4.656613e-10f * float(fHslider1);
		int iSlow8 = fSlow6 == 0.0f;
		float fSlow9 = float(fHslider2);
		float fSlow10 = 1.0f / std::max<float>(1.0f, fConst11 * fSlow9);
		float fSlow11 = float(fHslider3);
		float fSlow12 = fConst16 * fSlow0;
		float fSlow13 = 1.0f / std::max<float>(1.0f, fConst17 * fSlow9);
		float fSlow14 = fConst21 * fSlow0;
		float fSlow15 = 1.0f / std::max<float>(1.0f, fConst0 * fSlow9);
		float fSlow16 = float(fHslider4);
		float fSlow17 = fConst25 * fSlow0;
		float fSlow18 = 0.82f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow6;
			iRec2[0] = (fSlow6 > fVec1[1]) + (fSlow6 <= fVec1[1]) * (iRec2[1] + (iRec2[1] > 0));
			float fTemp0 = float(iRec2[0]);
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec1[0] = fSlow7 * float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) - fSlow5 * (fSlow4 * fRec1[2] + fSlow2 * fRec1[1]);
			iRec4[0] = iSlow8 * (iRec4[1] + 1);
			float fTemp1 = float(iRec4[0]);
			fRec5[0] = fSlow6 + fRec5[1] * float(fVec1[1] >= fSlow6);
			int iTemp2 = 1 - iVec0[1];
			float fTemp3 = fSlow11 * std::max<float>(0.0f, std::min<float>(fConst14 * fTemp0, fConst15 * (fConst13 - fTemp0) + 1.0f)) + 1.0f;
			float fTemp4 = ((iTemp2) ? 0.0f : fRec7[1] + fSlow12 * fTemp3);
			fRec7[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp2) ? 0.0f : fRec8[1] + fSlow14 * fTemp3);
			fRec8[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp2) ? 0.0f : fRec9[1] + fConst25 * (fSlow16 + fSlow0 * fTemp3));
			fRec9[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = ((iTemp2) ? 0.0f : fRec10[1] + fSlow17 * fTemp3);
			fRec10[0] = fTemp7 - std::floor(fTemp7);
			fRec0[0] = fSlow18 * (0.42f * (ftbl0GamelanGongSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec10[0]), 65535))] + ftbl0GamelanGongSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))]) * std::max<float>(0.0f, std::min<float>(fConst24 * fRec5[0], std::max<float>(fSlow15 * (fConst23 - fRec5[0]) + 1.0f, 0.0f)) * (1.0f - fConst22 * fTemp1)) + 0.3f * ftbl0GamelanGongSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst20 * fRec5[0], std::max<float>(fSlow13 * (fConst19 - fRec5[0]) + 1.0f, 0.0f)) * (1.0f - fConst18 * fTemp1)) + 0.15f * ftbl0GamelanGongSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst14 * fRec5[0], std::max<float>(fSlow10 * (fConst13 - fRec5[0]) + 1.0f, 0.0f)) * (1.0f - fConst12 * fTemp1)) + fSlow5 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1])) - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp8 = fConst26 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp8);
			output1[i0] = FAUSTFLOAT(fTemp8);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
